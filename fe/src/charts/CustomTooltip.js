import { DefaultTooltipContent } from 'recharts/lib/component/DefaultTooltipContent';

const CustomTooltip = props => {
    if (!props.active) {
        return null
    }
  
    // Add the new label here with the label prop
    const day = props.payload[0].payload.day
    const hour = props.payload[0].payload.hour
    return <DefaultTooltipContent {...props} label={`${day} ${hour}h`}/>;
  };

export default CustomTooltip