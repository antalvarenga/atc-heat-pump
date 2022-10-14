import { ResponsiveContainer, Tooltip } from "recharts";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import { DefaultTooltipContent } from 'recharts/lib/component/DefaultTooltipContent';
import { colors, margin } from './generalProps';
import CustomTooltip from './CustomTooltip';
import CustomAxisTick from './CustomAxisTick';

function formatModeAxis(value) {
    switch(value) {
      case 2:
        return "Comfort";
      case 1:
        return "Eco";
      case 0:
        return "Off";
      default:
        return ""
    }
  }

const formatter = (value, name, props) => {
  let formattedName;
  let formattedValue;
  switch (name){
    case "mode":
      formattedName = "Controlo optimizado"
      formattedValue = formatModeAxis(value)
      break;
    case "Standard_Mode":
      formattedName = "Funcionamento típico"
      formattedValue = formatModeAxis(value)
      break;
    case "ExternalTemperature":
      formattedName = "Temperatura exterior"
      formattedValue = value + " ºC"
      break;
    default:
      formattedName = name
  }
  return [formattedValue, formattedName]
}

const ModeLineChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <LineChart width={1000} height={400} data={props.data} margin={margin}>
            <Line
                type="monotone"
                dataKey={props.yaxis}
                stroke={colors.green}
                yAxisId="left"
            />
            <Line
                type="monotone"
                dataKey={props.yaxisStd}
                stroke={colors.blue}
                yAxisId="left"
            />
            <Line
                type="monotone"
                dataKey="ExternalTemperature"
                stroke={colors.red}
                yAxisId="right"
            />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis interval="preserveStartEnd" dataKey={props.isSingleDay ? "hour" : "Date"} tick={<CustomAxisTick isSingleDay={props.isSingleDay}/>}/>
            <YAxis yAxisId="left" dataKey="mode" tickCount={3} tickFormatter={formatModeAxis}/>
            <YAxis yAxisId="right" orientation="right" dataKey="ExternalTemperature"/>
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
        </LineChart>
    </ResponsiveContainer>
}

export default ModeLineChart