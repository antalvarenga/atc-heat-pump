import logo from "./logo.svg";
import "./App.css";
import data from "./charts/data.json";
import Example from "./charts/ZoomChart";
import ModeLineChart from "./charts/ModeLineChart";
import DefaultLineChart from "./charts/DefaultLineChart";
import AreaChart from "./charts/AreaChart";

function App() {
    return (
        <div className="App">
            <div>
                <h2>Modo de Funcionamento</h2>
                <ModeLineChart data={data} yaxis="mode"/>
            </div>
            <div>
                <h2>Temperatura (ºC)</h2>
                <DefaultLineChart data={data} yaxis="exterior_temperature"/>
            </div>
            <div>
                <h2>Comfort Score</h2>
                <AreaChart data={data} yaxis="Accumulated_daily_comfort_score_until_that_hour" xaxis="day"/>
            </div>
            <div>
                <h2>Potência (kW)</h2>
                <DefaultLineChart data={data} yaxis="Consumption_for_that_hour" xaxis="day"/>
            </div>
            <div>
                <h2>Consumo Energético (kWh)</h2>
                <AreaChart data={data} yaxis="Accumulated_daily_consumption_until_that_hour" xaxis="day"/>
            </div>
            <div>
                <h2>Custo Energético Acumulado (€)</h2>
                <AreaChart data={data} yaxis="accumulated_energy_cost_that_hour" xaxis="day"/>
            </div>

        </div>
    );
}

export default App;
