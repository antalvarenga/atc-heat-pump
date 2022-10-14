import axios from "axios";
import "./App.css";
import ModeLineChart from "./charts/ModeLineChart";
import DefaultLineChart from "./charts/DefaultLineChart";
import AreaChart from "./charts/AreaChart";
import Card from "@mui/material/Card";
import { useEffect, useState } from "react";
import { getHourlyData } from "./api";
import BasicDatePicker from "./ui/BasicDatePicker";
import MultipleSelect from "./ui/MultipleSelect";
import Checkbox from '@mui/material/Checkbox';

const cardStyles = {
    sx: {
        margin: "20px 0",
        padding: "30px",
    },
};

const initialCharts = [
    "Modo de Funcionamento",
    "Temperatura",
    "Comfort Score",
    "Potência",
    "Consumo Energético",
    "Custo Energético Acumulado",
];


function App() {
    const [startDate, setStartDate] = useState("2021-12-01");
    const [endDate, setEndDate] = useState("2021-12-31");
    const [data, setData] = useState(null);
    const [charts, setCharts] = useState(initialCharts);
    const [showTotals, setShowTotals] = useState(false);

    useEffect(() => {
        async function getData() {
            const newData = await getHourlyData({
                start_date: startDate,
                end_date: endDate,
            });
            setData(newData);
        }
        getData();
        console.log("useEffect");
    }, [startDate, endDate]);

    let isSingleDay = startDate === endDate;

    const onCheckboxChange = (event) => {
        setShowTotals(event.target.checked)
    }

    return (
        <div className="App">
            <div>
                <h1>Algoritmo de Controlo de uma Bomba de Calor</h1>
                <h5>By Cloud Team</h5>
            </div>
            <div>
                <p>
                    Os gráficos seguintes são para a cidade de Bragança, em
                    dezembro de 2021.
                </p>
            </div>
            <div style={{ display: "flex", flexDirection: "row", alignItems: "center", justifyContent:"flex-start" }}>
                <div className="select-item-container">   
                    <BasicDatePicker
                    label="Data inicial"
                    initialValue={startDate}
                    onSetDate={setStartDate}
                     />
                </div>

                <div className="select-item-container">   
                    <BasicDatePicker
                        label="Data final"
                        initialValue={endDate}
                        onSetDate={setEndDate}
                    />
                </div>
                <div className="select-item-container multiple-select">   
                    <MultipleSelect
                        selectedList={charts}
                        setSelectedList={setCharts}
                        list={initialCharts}
                    />
                </div>
            </div>
            <div style={{textAlign: "left"}}>
                <Checkbox onChange={onCheckboxChange}/> Ver totais 
            </div> 
            {data && (
                <div>
                    {charts.includes("Modo de Funcionamento") && (
                        <Card {...cardStyles}>
                            <h2>Modo de Funcionamento</h2>
                            <ModeLineChart
                                data={data}
                                yaxis="mode"
                                yaxisStd="Standard_Mode"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Temperatura") && (
                        <Card {...cardStyles}>
                            <h2>Temperatura (ºC)</h2>
                            <DefaultLineChart
                                data={data}
                                yaxis="exterior_temperature"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Comfort Score") && (
                        <Card {...cardStyles}>
                            <h2>Comfort Score</h2>
                            <AreaChart
                                data={data}
                                yaxis="Accumulated_daily_comfort_score_until_that_hour"
                                yaxisStd="Standard_Accumulated_daily_comfort_score_until_that_hour"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Potência") && (
                        <Card {...cardStyles}>
                            <h2>Potência (kW)</h2>
                            <DefaultLineChart
                                data={data}
                                yaxis="Consumption_for_that_hour"
                                yaxisStd="Standard_Consumption_for_that_hour"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Consumo Energético") && (
                        <Card {...cardStyles}>
                            <h2>Consumo Energético (kWh)</h2>
                            <AreaChart
                                data={data}
                                yaxis="Accumulated_daily_consumption_until_that_hour"
                                yaxisStd="Standard_Accumulated_daily_consumption_until_that_hour"
                                xaxis="day"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Custo Energético Acumulado") && (
                        <Card {...cardStyles}>
                            <h2>Custo Energético Acumulado (€)</h2>
                            <AreaChart
                                data={data}
                                yaxis="accumulated_energy_cost_that_hour"
                                yaxisStd="Standard_Accumulated_daily_energy_cost_until_that_hour"
                                xaxis="day"
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                </div>
            )}
        </div>
    );
}

export default App;
