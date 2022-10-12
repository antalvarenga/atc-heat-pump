import { Area, ReferenceLine, ResponsiveContainer } from "recharts";
import { AreaChart, Tooltip, CartesianGrid, XAxis, YAxis } from 'recharts';
import { colors, margin } from './generalProps';
import CustomTooltip from './CustomTooltip';
import CustomAxisTick from './CustomAxisTick';

const formatter = (value, name, props) => {
    console.log("name", name)
    let formattedName;
    let formattedValue;
    switch (name){
      case "Accumulated_daily_consumption_until_that_hour":
        formattedName = "Consumo Energético Acumulado"
        formattedValue = Math.round(value * 1000) / 1000 + " kWh"
        break;
      case "Accumulated_daily_comfort_score_until_that_hour":
        formattedName = "Comfort Score Acumulado"
        formattedValue = value
        break;
      case "accumulated_energy_cost_that_hour":
        formattedName = "Custo Energético Acumulado"
        formattedValue = Math.round(value * 100) / 100 + " €"
        break;
      default:
        formattedName = name
        formattedValue = value
    }
    console.log("formattedName", formattedName)
    console.log("formattedValue", formattedValue)
    return [formattedValue, formattedName]
  }

const DefaultAreaChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <AreaChart width={1000} height={400} data={props.data} margin={margin}>
            <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={colors.green} stopOpacity={0.8}/>
                <stop offset="95%" stopColor={colors.green} stopOpacity={0}/>
                </linearGradient>
            </defs>
            <XAxis dataKey={props.xaxis} tick={<CustomAxisTick />}/>
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
            <Area type="monotone" dataKey={props.yaxis} stroke={colors.green} fillOpacity={1} fill="url(#colorUv)" />
            <ReferenceLine y={124} stroke="green" label="Minimum Comfort Score" />
        </AreaChart>
    </ResponsiveContainer>
}

export default DefaultAreaChart