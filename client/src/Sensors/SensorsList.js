import React, {Component} from 'react';
import './SensorsList.css';
import SensorItem  from './SensorItem';
import { Sensor } from './SensorItem';
import { popupAddNewSensor, SensorPopup } from "./SensorPopup";

const displayProperties = [
    'ID',
    'Serial number',
    'Name',
    'Communication status',
    'Description',
    'Actions'
]

class SensorsList extends Component {
    state = {
        sensors: [
            new Sensor('0x1234', 'Climate', 0, 'Informing about humidity and temperature'),
            new Sensor('0x4321', 'Leak', 1, 'Informing about water leaking in home'),
            new Sensor('0x1234', 'Gas', 0, 'Informing about humidity and temperature'),
            new Sensor('0x4321', 'Smoke', 1, 'Informing about water leaking in home'),
            new Sensor('0x1234', 'Tamper', 0, 'Informing about humidity and temperature'),
            new Sensor('0x1234', 'Unknown', 0, 'Informing about humidity and temperature'),
        ]
    }

    constructor(props) {
        super();
    }

    addSensorItem(sn, name="Generic", status=true, description="Generic device, please append new data here") {
        this.state.sensors.push(new Sensor(sn, name, status, description));
        this.setState( { sensors: this.state.sensors } );
    }

    /* Debug part only, will be replaced by socket.io functionality */
    onAddItem() {
        const sn = "0xFFAB8271940302";
        console.log(this);
        popupAddNewSensor(sn, this.addSensorItem.bind(this));

    }

    onRemoveItem(sensorId) {
        this.setState({sensors: this.state.sensors.filter(item => (item.id !== sensorId))});
    }

    render() {
        return (
            <div>
                <table id='sensors'>
                    <thead key="thead">
                        <tr>
                            { displayProperties.map( (sensorProperty) =>
                                <th> { sensorProperty } </th>
                            )}
                        </tr>
                    </thead>
                    <tbody key="tbody">
                        { this.state.sensors.map( ( sensor ) =>
                            <SensorItem data={sensor} onRemove={this.onRemoveItem.bind(this)} />
                        )}
                    </tbody>
                </table>
                <SensorPopup />

                {/* Debug part only, will be replaced by socket.io functionality */}
                <button className="sensor-btn-delete" onClick={this.onAddItem.bind(this)}>Simulate adding new device</button>
            </div>
        )
    }
}

export default SensorsList;