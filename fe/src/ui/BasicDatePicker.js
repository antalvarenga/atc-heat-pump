import * as React from 'react';
import TextField from '@mui/material/TextField';
import { AdapterMoment } from '@mui/x-date-pickers/AdapterMoment';
import { LocalizationProvider } from '@mui/x-date-pickers/LocalizationProvider';
import { DatePicker } from '@mui/x-date-pickers/DatePicker';

export default function BasicDatePicker(props) {
  const [value, setValue] = React.useState(props.initialValue);

  return (
    <LocalizationProvider dateAdapter={AdapterMoment}>
      <DatePicker
        label={props.label}
        value={value}
        onChange={(newValue) => {
          console.log("NewValue", newValue)
          console.log("NewValue formatted", newValue.format("YYYY-MM-DD"))
          setValue(newValue);
          props.onSetDate(newValue.format("YYYY-MM-DD"));
        }}
        renderInput={(params) => <TextField {...params} />}
      />
    </LocalizationProvider>
  );
}
