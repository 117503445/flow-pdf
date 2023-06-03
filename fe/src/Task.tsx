import { useParams } from 'react-router-dom';
import { useState, useEffect } from 'react';

function Task() {

    const { id } = useParams();
    const [timer, setTimer] = useState(0);
    const [status, setStatus] = useState("uncreated");


    async function fetchTask() {
        const response = await fetch(import.meta.env.VITE_BE_HOST + `/static/${id}/task.json`)
        if (response.status != 200) {
            return
        }
        const data = await response.json();
        const s = data['status'];
        setStatus(s);
        if (s == "done") {
            const url = import.meta.env.VITE_BE_HOST + `/static/${id}/output/index.html`;
            console.log(url);
            window.location.replace(url);
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