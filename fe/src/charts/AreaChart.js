import { Area, ReferenceLine, ResponsiveContainer } from "recharts";
import { AreaChart, Tooltip, CartesianGrid, XAxis, YAxis } from 'recharts';
import { margin } from './generalProps';
const DefaultAreaChart = (props) => {
    return <ResponsiveContainer width="100%" height={400}>
        <AreaChart width={1000} height={400} data={props.data} margin={margin}>
            <defs>
                <linearGradient id="colorUv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#8884d8" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#8884d8" stopOpacity={0}/>
                </linearGradient>
                <linearGradient id="colorPv" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#82ca9d" stopOpacity={0.8}/>
                <stop offset="95%" stopColor="#82ca9d" stopOpacity={0}/>
                </linearGradient>
            </defs>
            <XAxis dataKey={props.xaxis} />
            <YAxis />
            <CartesianGrid strokeDasharray="3 3" />
            <Tooltip />
            <Area type="monotone" dataKey={props.yaxis} stroke="#8884d8" fillOpacity={1} fill="url(#colorUv)" />
            <ReferenceLine y={124} stroke="green" label="Minimum Comfort Score" />
        </AreaChart>
    </ResponsiveContainer>
}

export default DefaultAreaChart