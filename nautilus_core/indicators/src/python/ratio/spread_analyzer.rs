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

use nautilus_core::python::to_pyvalue_err;
use nautilus_model::{
    data::quote::QuoteTick, enums::PriceType, identifiers::InstrumentId,
    python::identifiers::instrument_id,
};
use pyo3::prelude::*;

use crate::{indicator::Indicator, ratio::spread_analyzer::SpreadAnalyzer};

#[pymethods]
impl SpreadAnalyzer {
    #[new]
    fn py_new(instrument_id: InstrumentId, capacity: usize) -> PyResult<Self> {
        Self::new(capacity, instrument_id).map_err(to_pyvalue_err)
    }

    fn __repr__(&self) -> String {
        format!("SpreadAnalyzer({})", self.capacity)
    }

    #[getter]
    #[pyo3(name = "name")]
    fn py_name(&self) -> String {
        self.name()
    }

    #[getter]
    #[pyo3(name = "capacity")]
    fn py_capacity(&self) -> usize {
        self.capacity
    }

    #[getter]
    #[pyo3(name = "current")]
    fn py_current(&self) -> f64 {
        self.current
    }

    #[getter]
    #[pyo3(name = "average")]
    fn py_average(&self) -> f64 {
        self.average
    }

    #[getter]
    #[pyo3(name = "initialized")]
    fn py_initialized(&self) -> bool {
        self.initialized
    }

    #[pyo3(name = "has_inputs")]
    fn py_has_inputs(&self) -> bool {
        self.has_inputs()
    }

    #[pyo3(name = "handle_quote_tick")]
    fn py_handle_quote_tick(&mut self, quote: &QuoteTick) {
        self.handle_quote_tick(quote);
    }

    #[pyo3(name = "reset")]
    fn py_reset(&mut self) {
        self.reset();
    }
}
