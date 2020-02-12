import React from 'react';

export class Sensor {
    static id = 0;

    constructor(sn, name, status, description="") {
        this.id = Sensor.id++;
        this.name = name;
        this.status = status;
        this.description = description;
        this.sn = sn;
    }
}

export default function SensorItem( {data, onRemove} ) {
    const paramNum = Object.keys(data).length;

    return (
        <tr key={10000 - data.id}>
            <td key={paramNum * data.id    }> {data.id} </td>
            <td key={paramNum * data.id + 1}> {data.sn} </td>
            <td key={paramNum * data.id + 2}> {data.name} </td>
            <td key={paramNum * data.id + 3} 
                className={data.status ? "sensor-status-active" : "sensor-status-lost"}>
                {data.status ? "ACTIVE" : "LOST"}
            </td>
            <td key={paramNum * data.id + 4}> {data.description} </td>
            <td key={paramNum * data.id + 5}> 
                <button className="sensor-btn-delete" onClick={() => onRemove(data.id)}>Remove</button>
            </td>
        </tr>
    )
}