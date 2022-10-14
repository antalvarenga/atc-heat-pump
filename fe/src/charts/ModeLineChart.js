import { ResponsiveContainer, Tooltip } from "recharts";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import { DefaultTooltipContent } from 'recharts/lib/component/DefaultTooltipContent';
import { colors, margin } from './generalProps';
import CustomTooltip from './CustomTooltip';
import CustomAxisTick from './CustomAxisTick';

function formatYAxis(value) {
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
  switch (name){
    case "mode":
      formattedName = "Controlo optimizado"
      break;
    case "Standard_Mode":
      formattedName = "Funcionamento típico"
      break;
    default:
      formattedName = name
  }
  return [formatYAxis(value), formattedName]
}

const ModeLineChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <LineChart width={1000} height={400} data={props.data} margin={margin}>
            <Line
                type="monotone"
                dataKey={props.yaxis}
                stroke={colors.green}
            />
            <Line
                type="monotone"
                dataKey={props.yaxisStd}
                stroke={colors.blue}
            />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis interval="preserveStartEnd" dataKey={props.isSingleDay ? "hour" : "Date"} tick={<CustomAxisTick isSingleDay={props.isSingleDay}/>}/>
            <YAxis dataKey="mode" tickCount={3} tickFormatter={formatYAxis}/>
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
        </LineChart>
    </ResponsiveContainer>
}

export default ModeLineChart