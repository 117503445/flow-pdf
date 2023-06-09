import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Task() {

    const { id } = useParams();
    const [timer, setTimer] = useState(0);
    const [status, setStatus] = useState("uncreated");

    let statusURL = import.meta.env.VITE_BE_HOST + `/static/${id}/task.json`
    let resultURL = import.meta.env.VITE_BE_HOST + `/static/${id}/output/index.html`;

    const VITE_STATIC_HOST = import.meta.env.VITE_STATIC_HOST;

    if (VITE_STATIC_HOST != null && VITE_STATIC_HOST != "") {
        statusURL = VITE_STATIC_HOST + `/output/${id}/task.json`
        resultURL = VITE_STATIC_HOST + `/output/${id}/output/index.html`
    }

    console.log("statusURL", statusURL);
    console.log("resultURL", resultURL);

    async function fetchTask() {
        const response = await fetch(statusURL)
        if (response.status != 200) {
            return
        }
        const data = await response.json();
        const s = data['status'];
        setStatus(s);

        if (s == "done") {
            window.location.replace(resultURL);
        } else if (s == "error") {
            console.log("clear timer", timer);
            clearInterval(timer);
        }
    }

    useEffect(() => {
        setTimer(setInterval(async () => {
            await fetchTask();
        }, 3000));

        return () => clearInterval(timer);
    }, []);

    return (
        <>
            <p> Task Page {id}</p>
            <p> Status: {status}</p>
        </>
    )
}

export default Task