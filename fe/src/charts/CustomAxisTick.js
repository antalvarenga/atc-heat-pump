const CustomAxisTick = (props) => {
    const { x, y, stroke, payload } = props;
    console.log("payload", payload)
    console.log("customText", props.customText)
    return (
        <g transform={`translate(${x},${y})`}>
            <text
                x={0}
                y={0}
                dy={16}
                textAnchor="end"
                fill="#666"
                {...(props.isSingleDay ? {} : {transform: "rotate(-35)"})}
            >

                {payload.value}{props.isSingleDay ? "h" : ""}
            </text>
        </g>
    );
};

export default CustomAxisTick;