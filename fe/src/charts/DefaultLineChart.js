import { ResponsiveContainer, Tooltip } from "recharts";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import { colors, margin } from './generalProps';
import CustomTooltip from './CustomTooltip';
import CustomAxisTick from './CustomAxisTick';

const formatter = (value, name, props) => {
  console.log("name", name)
  let formattedName;
  let formattedValue;
  switch (name){
    case "exterior_temperature":
      formattedName = "Temperatura exterior"
      formattedValue = value + " ºC"
      break;
    case "Consumption_for_that_hour":
      formattedName = "Potência"
      formattedValue = value + " kW"
      break;
    default:
      formattedName = name
      formattedValue = value
  }
  console.log("formattedName", formattedName)
  console.log("formattedValue", formattedValue)
  return [formattedValue, formattedName]
}

const DefaultLineChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <LineChart width={1000} height={400} data={props.data} margin={margin}>
            <Line
                type="monotone"
                dataKey={props.yaxis}
                stroke={colors.green}
            />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis dataKey="day" tick={<CustomAxisTick />}/>
            <YAxis dataKey={props.yaxis}/>
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
        </LineChart>
    </ResponsiveContainer>
}

export default DefaultLineChart