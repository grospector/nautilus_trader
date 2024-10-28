// -------------------------------------------------------------------------------------------------
//  Copyright (C) 2015-2024 Nautech Systems Pty Ltd. All rights reserved.
//  https://nautechsystems.io
//
//  Licensed under the GNU Lesser General Public License Version 3.0 (the "License");
//  You may not use this file except in compliance with the License.
//  You may obtain a copy of the License at https://www.gnu.org/licenses/lgpl-3.0.en.html
//
//  Unless required by applicable law or agreed to in writing, software
//  distributed under the License is distributed on an "AS IS" BASIS,
//  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
//  See the License for the specific language governing permissions and
//  limitations under the License.
// -------------------------------------------------------------------------------------------------

use std::{cell::RefCell, collections::VecDeque, rc::Rc};

use nautilus_common::{
    clock::{set_clock, TestClock},
    messages::data::{DataClientResponse, DataResponse},
    timer::TimeEventHandlerV2,
};
use nautilus_model::data::GetTsInit;
use tokio::sync::mpsc::{UnboundedReceiver, UnboundedSender};

use super::DataEngine;

pub trait Runner {
    type Sender;

    fn new() -> Self;
    fn run(&mut self, engine: &mut DataEngine);
    fn get_sender(&self) -> Self::Sender;
}

pub trait SendResponse {
    fn send(&self, resp: DataResponse);
}

pub type DataResponseQueue = Rc<RefCell<VecDeque<DataClientResponse>>>;

pub struct BacktestRunner {
    queue: DataResponseQueue,
    #[cfg(feature = "clock_v2")]
    pub clock: Rc<RefCell<TestClock>>,
}

impl Runner for BacktestRunner {
    type Sender = DataResponseQueue;

    fn new() -> Self {
        #[cfg(feature = "clock_v2")]
        let clock = {
            let clock = Rc::new(RefCell::new(TestClock::new()));
            set_clock(clock.clone());
            clock
        };

        Self {
            queue: Rc::new(RefCell::new(VecDeque::new())),
            #[cfg(feature = "clock_v2")]
            clock,
        }
    }

    fn run(&mut self, engine: &mut DataEngine) {
        while let Some(resp) = self.queue.as_ref().borrow_mut().pop_front() {
            match resp {
                DataClientResponse::Response(resp) => engine.response(resp),
                DataClientResponse::Data(data) => {
                    #[cfg(feature = "clock_v2")]
                    {
                        // Advance clock time and collect all triggered events
                        // and there handlers
                        let handlers: Vec<TimeEventHandlerV2> = {
                            let mut guard = self.clock.borrow_mut();
                            guard.advance_time(data.ts_init(), true);
                            guard.by_ref().collect()
                        };

                        // Execut all handlers before processing the data
                        handlers.into_iter().for_each(TimeEventHandlerV2::run);
                    }

                    engine.process_data(data);
                }
            }
        }
    }

    fn get_sender(&self) -> Self::Sender {
        self.queue.clone()
    }
}

pub struct LiveRunner {
    resp_tx: UnboundedSender<DataClientResponse>,
    resp_rx: UnboundedReceiver<DataClientResponse>,
}

impl Runner for LiveRunner {
    type Sender = UnboundedSender<DataClientResponse>;

    fn new() -> Self {
        let (resp_tx, resp_rx) = tokio::sync::mpsc::unbounded_channel::<DataClientResponse>();
        Self { resp_tx, resp_rx }
    }

    fn run(&mut self, engine: &mut DataEngine) {
        // TODO: Listen to new events created by LiveTimers push on the heap
        while let Some(resp) = self.resp_rx.blocking_recv() {
            match resp {
                DataClientResponse::Response(resp) => engine.response(resp),
                DataClientResponse::Data(data) => engine.process_data(data),
            }
        }
    }

    fn get_sender(&self) -> Self::Sender {
        self.resp_tx.clone()
    }
}
