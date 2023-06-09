import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Task() {

    const { id } = useParams();
    const [timer, setTimer] = useState(0);
    const [status, setStatus] = useState("uncreated");


    async function fetchTask() {

        let statusURL = import.meta.env.VITE_BE_HOST + `/static/${id}/task.json`
        let resultURL = import.meta.env.VITE_BE_HOST + `/static/${id}/output/index.html`;

        if (import.meta.env.VITE_STATIC_HOST.length > 0) {
            statusURL = import.meta.env.VITE_STATIC_HOST + `/output/${id}/task.json`
            resultURL = import.meta.env.VITE_STATIC_HOST + `/output/${id}/output/index.html`
        }

        console.log("statusURL", statusURL);
        console.log("resultURL", resultURL);

        const response = await fetch(statusURL)
        if (response.status != 200) {
            return
        }
        const data = await response.json();
        const s = data['status'];
        setStatus(s);
        if (s == "done") {
            window.location.replace(resultURL);
        }
    }

    useEffect(() => {
        setTimer(setInterval(async () => {
            await fetchTask();
        }, 1000));

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