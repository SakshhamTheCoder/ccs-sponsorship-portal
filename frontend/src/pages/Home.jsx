import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faEnvelope, faPhone, faDollarSign, faCalendar } from '@fortawesome/free-solid-svg-icons';
import Button from '../components/Button';
import api from '../utils/APIClient';

const Home = () => {
    const [values, setValues] = useState({
        name: '',
        company_name: '',
        email: '',
        contact: '',
        amount: '',
        event: ''
    });

    const fieldsConfig = [
        { key: 'name', placeholder: 'Name', type: 'text', icon: faUser },
        { key: 'company_name', placeholder: 'Company Name', type: 'text', icon: faBuilding },
        { key: 'email', placeholder: 'Email', type: 'email', icon: faEnvelope },
        { key: 'contact', placeholder: 'Contact', type: 'tel', icon: faPhone },
        { key: 'amount', placeholder: 'Amount', type: 'number', icon: faDollarSign },
    ];

    const handleInputChange = (e, key) => {
        setValues({ ...values, [key]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Form Values:', values);
        api.post('/sponsorship/add', values).then((res) => {
            console.log('Response:', res);
        });
    };

    return (
        <div className="flex rounded-lg items-center w-full min-h-[calc(100vh-10rem)]">
            <div className="flex flex-col rounded-lg p-8 shadow-lg border-2 h-full w-full bg-container justify-center items-center md:p-16">
                <div className="text-4xl font-bold text-center">
                    CCS Sponsorship Portal
                </div>
                <hr className="my-6 border-2 rounded-lg w-1/2" />
                <form className="flex flex-col gap-4 w-full max-w-md mt-8" onSubmit={handleSubmit}>
                    {fieldsConfig.map(({ key, placeholder, type, icon }) => (
                        <div key={key} className="flex items-center border-2 border-gray-200 rounded-lg p-2 focus-within:border-primary">
                            <FontAwesomeIcon icon={icon} className="text-gray-500 mr-2" />
                            <input
                                className="w-full focus:outline-none"
                                type={type}
                                placeholder={placeholder}
                                value={values[key]}
                                onChange={(e) => handleInputChange(e, key)}
                            />
                        </div>
                    ))}
                    <div className="flex items-center border-2 border-gray-200 rounded-lg p-2 focus-within:border-primary">
                        <FontAwesomeIcon icon={faCalendar} className="text-gray-500 mr-2" />
                        <select
                            value={values.event}
                            onChange={(e) => handleInputChange(e, 'event')}
                            name="event"
                            className="w-full focus:outline-none"
                        >
                            <option value="" disabled selected>
                                Select Event
                            </option>
                            <option value="hacktu">HackTU 6.0</option>
                            <option value="helixweek">Helix Week</option>
                            <option value="codingcommunity">Coding Community</option>
                        </select>
                    </div>
                    <Button className="py-2 mt-4" isActive text="Submit" />
                </form>
            </div>
        </div>
    );
};

export default Home;
