import { ResponsiveContainer, Tooltip } from "recharts";
import { LineChart, Line, CartesianGrid, XAxis, YAxis } from 'recharts';
import { margin } from './generalProps';

const DefaultLineChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <LineChart width={1000} height={400} data={props.data} margin={margin}>
            <Line
                type="monotone"
                dataKey={props.yaxis}
                stroke="#8884d8"
            />
            <CartesianGrid stroke="#ccc" strokeDasharray="5 5" />
            <XAxis dataKey="day" />
            <YAxis dataKey={props.yaxis}/>
            <Tooltip />
        </LineChart>
    </ResponsiveContainer>
}

export default DefaultLineChart