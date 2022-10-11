import { ResponsiveContainer, Tooltip } from "recharts";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import { DefaultTooltipContent } from 'recharts/lib/component/DefaultTooltipContent';
import { margin } from './generalProps';

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
  return [formatYAxis(value), "Mode", props]
}

 const CustomTooltip = props => {
  if (!props.active) {
      return null
  }

  // Add the new label here with the label prop
  const day = props.payload[0].payload.day
  const hour = props.payload[0].payload.hour
  return <DefaultTooltipContent {...props} label={`${day} ${hour}h`}/>;
};

const ModeLineChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <LineChart width={1000} height={400} data={props.data} margin={margin}>
            <Line
                type="monotone"
                dataKey={props.yaxis}
                stroke="#8884d8"
            />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis dataKey="day" />
            <YAxis dataKey="mode" tickCount={3} tickFormatter={formatYAxis}/>
            <Tooltip content={<CustomTooltip formatter={formatter}/>} />
        </LineChart>
    </ResponsiveContainer>
}

export default ModeLineChart