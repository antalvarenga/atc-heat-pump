import logo from "./logo.svg";
import "./App.css";
import data from "./charts/data.json";
import Example from "./charts/ZoomChart";
import ModeLineChart from "./charts/ModeLineChart";
import DefaultLineChart from "./charts/DefaultLineChart";
import AreaChart from "./charts/AreaChart";
import Card from '@mui/material/Card';

const cardStyles = {
  sx: {
    margin: "40px 0",
    padding: "40px"
  } 
}

function App() {
    return (
        <div className="App">
            <div>
              <h1>Algoritmo de Controlo de uma Bomba de Calor</h1>
              <h5>By Cloud Team</h5>
            </div>
            <div>
              <p>Os gráficos seguintes são para a cidade de Bragança, em dezembro de 2021.</p>
            </div>
            <Card {...cardStyles}>
                <h2>Modo de Funcionamento</h2>
                <ModeLineChart data={data} yaxis="mode"/>
            </Card>
            <Card {...cardStyles}>
                <h2>Temperatura (ºC)</h2>
                <DefaultLineChart data={data} yaxis="exterior_temperature"/>
            </Card>
            <Card {...cardStyles}>
                <h2>Comfort Score</h2>
                <AreaChart data={data} yaxis="Accumulated_daily_comfort_score_until_that_hour" xaxis="day"/>
            </Card>
            <Card {...cardStyles}>
                <h2>Potência (kW)</h2>
                <DefaultLineChart data={data} yaxis="Consumption_for_that_hour" xaxis="day"/>
            </Card>
            <Card {...cardStyles}>
                <h2>Consumo Energético (kWh)</h2>
                <AreaChart data={data} yaxis="Accumulated_daily_consumption_until_that_hour" xaxis="day"/>
            </Card>
            <Card {...cardStyles}>
                <h2>Custo Energético Acumulado (€)</h2>
                <AreaChart data={data} yaxis="accumulated_energy_cost_that_hour" xaxis="day"/>
            </Card>

        </div>
    );
}

export default App;
