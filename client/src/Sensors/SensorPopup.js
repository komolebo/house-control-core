import React, {Component} from 'react';
import Popup from 'react-popup';

import './SensorPopup.css';


export function popupAddNewSensor(sn, callback, name="GenericName", description="Nothing") {
    Popup.plugins().prompt(sn, name, 'Device name', function (value) {
         callback(sn, value);
    });
}

class Prompt extends React.Component {
    constructor(props) {
        super(props);

        this.state = {
            value: this.props.defaultValue
        };

        this.onChange = (e) => this._onChange(e);
    }

    componentDidUpdate(prevProps, prevState) {
        if (prevState.value !== this.state.value) {
            this.props.onChange(this.state.value);
        }
    }

    _onChange(e) {
        let value = e.target.value;

        this.setState({value: value});
    }

    render() {
        return <input type="text" placeholder={this.props.placeholder} className="mm-popup__input" value={this.state.value} onChange={this.onChange} />;
    }
}


Popup.registerPlugin('prompt', function (sn, name, defaultValue, callback) {
    let promptSensorName = null;
    let onPromptChange = function (value) {
        promptSensorName = value;
    };

    this.create({
        title: `Set name for SN=${sn}`,
        content: <Prompt onChange={onPromptChange} placeholder={`Device name for ${name}`} value={defaultValue} />,
        buttons: {
            left: ['cancel'],
            right: [{
                text: 'Save',
                key: '⌘+s',
                className: 'success',
                action: function () {
                    callback(promptSensorName);
                    Popup.close();
                }
            }]
        }
    });
});

export var SensorPopup = Popup;