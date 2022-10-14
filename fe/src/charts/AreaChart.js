import { Area, Legend, ReferenceLine, ResponsiveContainer } from "recharts";
import { AreaChart, Tooltip, CartesianGrid, XAxis, YAxis } from 'recharts';
import { colors, margin } from './generalProps';
import CustomTooltip from './CustomTooltip';
import CustomAxisTick from './CustomAxisTick';

const formatter = (value, name, props) => {
    let formattedName;
    let formattedValue;
    switch (name){
      case "AccumulatedEnergyConsumption":
        formattedName = "Controlo optimizado"
        formattedValue = Math.round(value * 1000) / 1000 + " kWh"
        break;
      case "AccumulatedComfortScore":
        formattedName = "Controlo optimizado"
        formattedValue = value
        break;
      case "Standard_AccumulatedComfortScore":
        formattedName = "Funcionamento típico"
        formattedValue = value
        break;
      case "AccumulatedCost":
        formattedName = "Controlo optimizado"
        formattedValue = Math.round(value * 100) / 100 + " €"
        break;
      case "Standard_AccumulatedCost":
        formattedName = "Funcionamento típico"
        formattedValue = Math.round(value * 100) / 100 + " €"
        break;
      case "Standard_AccumulatedEnergyConsumption":
        formattedName = "Funcionamento típico"
        formattedValue = Math.round(value * 100) / 100 + " kWh"
        break;
      default:
        formattedName = name
        formattedValue = value
    }
    return [formattedValue, formattedName]
  }

const DefaultAreaChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <AreaChart width={1000} height={400} data={props.data} margin={margin}>
            <defs>
                <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.green} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={colors.green} stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorBlue" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor={colors.blue} stopOpacity={0.8}/>
                  <stop offset="95%" stopColor={colors.blue} stopOpacity={0}/>
                </linearGradient>
            </defs>
            <XAxis interval="preserveStartEnd" dataKey={props.isSingleDay ? "hour" : "Date"} tick={<CustomAxisTick isSingleDay={props.isSingleDay}/>}/>
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
            <Area type="monotone" dataKey={props.yaxis} stroke={colors.green} fillOpacity={1} fill="url(#colorGreen)" />
            <Area type="monotone" dataKey={props.yaxisStd} stroke={colors.blue} fillOpacity={1} fill="url(#colorBlue)" />
            {/* TODO */}
            {/* <Legend /> */}
            {props.hasReferenceLine && <ReferenceLine y={124} stroke="green" label="Minimum Comfort Score" />}
        </AreaChart>
    </ResponsiveContainer>
}

export default DefaultAreaChart