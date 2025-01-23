import React, { useEffect, useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUser, faBuilding, faEnvelope, faPhone, faDollarSign, faCalendar, faRupeeSign, faMoneyBill1Wave } from '@fortawesome/free-solid-svg-icons';
import Button from '../components/Button';
import api from '../utils/APIClient';
import { useNavigate } from 'react-router-dom';
import { toWords } from "number-to-words";

const Home = () => {
    const [loading, setLoading] = useState(false);
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
        { key: 'amount', placeholder: 'Amount', type: 'number', icon: faRupeeSign },
    ];

    const handleInputChange = (e, key) => {
        setValues({ ...values, [key]: e.target.value });
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        if (loading) return;
        if (values.event === "" || values.amount === "") return;
        setLoading(true);
        api.post('/sponsorship/add', values).then((res) => {
            let sponserId = res.id;
            api.post('/payments/create', { amount: parseFloat(values.amount), sponsor_id: sponserId }).then((res) => {
                window.location.href = res.pay_page_url;
            }).finally(() => {
                setLoading(false);
            });
        }).finally(() => {
            setLoading(false);
        });
    };

    const [words, setWords] = useState("");

    useEffect(() => {
        if (values.amount === "") {
            setWords("");
            return;
        }
        let text = toWords(values.amount);
        setWords(text.charAt(0).toUpperCase() + text.slice(1));
    }
        , [values.amount]);

    return (
        <div className="flex rounded-lg items-center w-full min-h-[calc(100vh-10rem)]">
            <div className="flex flex-col rounded-lg p-8 shadow-lg border-2 h-full w-full bg-container justify-center items-center md:p-16">
                <div className="text-4xl font-bold text-center">
                    CCS Sponsorship Portal
                </div>
                <hr className="my-6 border-2 rounded-lg w-1/2" />
                <form className="flex flex-col gap-6 w-full max-w-md mt-8" onSubmit={handleSubmit}>
                    {fieldsConfig.map(({ key, placeholder, type, icon }) => (
                        <div
                            key={key}
                            className="flex items-center bg-white border-2 border-gray-200 rounded-lg px-4 py-2 focus-within:border-primary"
                        >
                            <FontAwesomeIcon icon={icon} className="text-gray-500" />
                            <input
                                className="w-full pl-4 text-sm focus:outline-none"
                                type={type}
                                placeholder={placeholder}
                                value={values[key]}
                                onChange={(e) => handleInputChange(e, key)}
                            />
                        </div>
                    ))}
                    <div className="flex items-center bg-white border-2 border-gray-200 rounded-lg px-4 py-2 focus-within:border-primary">
                        <FontAwesomeIcon icon={faCalendar} className="text-gray-500" />
                        <select
                            value={values.event}
                            onChange={(e) => handleInputChange(e, 'event')}
                            name="event"
                            className="w-full pl-4 text-sm bg-transparent focus:outline-none"
                        >
                            <option value="" disabled>
                                Select Event
                            </option>
                            <option value="hacktu">HackTU 6.0</option>
                            <option value="helixweek">Helix Week</option>
                            <option value="codingcommunity">Coding Community</option>
                        </select>
                    </div>
                    <p>Paying: Rs {words !== "" ? words : "Zero"} Only</p>
                    <Button icon={faMoneyBill1Wave} className="py-2" isActive text="Submit" disabled={loading} />
                </form>
            </div>
        </div>
    );
};

export default Home;
