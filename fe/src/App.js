import axios from "axios";
import "./App.css";
import ModeLineChart from "./charts/ModeLineChart";
import DefaultLineChart from "./charts/DefaultLineChart";
import AreaChart from "./charts/AreaChart";
import Card from "@mui/material/Card";
import { useEffect, useState } from "react";
import { getDailyData, getHourlyData } from "./api";
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
            let newData
            if (showTotals) {
                newData = await getDailyData({
                    start_date: startDate,
                    end_date: endDate,
                });
            } else {
                newData = await getHourlyData({
                    start_date: startDate,
                    end_date: endDate,
                });
            }
            setData(newData);
        }
        getData();
        console.log("useEffect");
    }, [startDate, endDate, showTotals]);

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
                    {charts.includes("Modo de Funcionamento") && !showTotals && (
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
                                yaxis={showTotals ? "MaxExternalTemperature" : "ExternalTemperature"}
                                yaxisStd={showTotals ? "MinExternalTemperature" : null}
                                isSingleDay={isSingleDay}
                            />
                        </Card>
                    )}
                    {charts.includes("Comfort Score") && (
                        <Card {...cardStyles}>
                            <h2>Comfort Score</h2>
                            <AreaChart
                                data={data}
                                yaxis="AccumulatedComfortScore"
                                yaxisStd="Standard_AccumulatedComfortScore"
                                isSingleDay={isSingleDay}
                                {...(showTotals ? {hasReferenceLine: false} : {hasReferenceLine: true})}
                            />
                        </Card>
                    )}
                    {charts.includes("Potência") && (
                        <Card {...cardStyles}>
                            <h2>Potência (kW)</h2>
                            <DefaultLineChart
                                data={data}
                                yaxis="EnergyConsumption"
                                yaxisStd="Standard_EnergyConsumption"
                                isSingleDay={isSingleDay}
                                hasTemperature
                            />
                        </Card>
                    )}
                    {charts.includes("Consumo Energético") && (
                        <Card {...cardStyles}>
                            <h2>Consumo Energético (kWh)</h2>
                            <AreaChart
                                data={data}
                                yaxis="AccumulatedEnergyConsumption"
                                yaxisStd="Standard_AccumulatedEnergyConsumption"
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
                                yaxis="AccumulatedCost"
                                yaxisStd="Standard_AccumulatedCost"
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
