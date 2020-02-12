import React, {Component} from 'react';
import './SensorsList.css';
import SensorItem  from './SensorItem';
import { Sensor } from './SensorItem';


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

    onRemoveItem(sensorId) {
        this.setState({sensors: this.state.sensors.filter(item => (item.id !== sensorId))});
    }

    render() {
        return (
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
        )
    }
}

export default SensorsList;