import { DefaultTooltipContent } from 'recharts/lib/component/DefaultTooltipContent';

const CustomTooltip = props => {
    if (!props.active) {
        return null
    }
  
    // Add the new label here with the label prop
    let label = ""
    if (props.payload[0]) {
      const day = props.payload[0].payload.Date
      const hour = props.payload[0].payload.hour
      label = hour ? `${day} ${hour}h` : day

    }
    return <DefaultTooltipContent {...props} label={label}/>;
  };

export default CustomTooltip