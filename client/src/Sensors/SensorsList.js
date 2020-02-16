import React, {Component} from 'react';
import './SensorsList.css';
import SensorItem  from './SensorItem';
import { Sensor } from './SensorItem';
import { popupAddNewSensor, SensorPopup } from "./SensorPopup";
import axios from 'axios';

axios.defaults.baseURL = 'http://192.168.1.12:8000/';


const displayProperties = [
    'ID',
    'Serial number',
    'Name',
    'Communication status',
    'Description',
    'Actions'
]

class SensorsList extends Component {
    state = { sensors: [] }

    constructor(props) {
        super();
        axios
            .get('api/sensors/')
            .then(response => this.setState({sensors: response.data}))
            .catch(err => console.log(err));
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
        console.log("removing " + sensorId);
        axios
            .delete('api/sensors/' + sensorId, {data: sensorId})
            .then(res => {
                this.setState({sensors: this.state.sensors.filter(item => (item.id !== sensorId))});
            })
            .catch(err => {
                console.log(err);
            })
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