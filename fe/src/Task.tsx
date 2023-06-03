import { useParams } from 'react-router-dom';
import React, { useState, useEffect } from 'react';

function Task() {

    const { id } = useParams();
    const [timer, setTimer] = useState(0);
    const [status, setStatus] = useState("uncreated");


    async function fetchTask() {
        const response = await fetch(`http://localhost:8000/static/${id}/task.json`)
        if (response.status != 200) {
            return
        }
        const data = await response.json();
        setStatus(data['status'])
    }

    useEffect(() => {
        setTimer(setInterval(async () => {
            await fetchTask();
            if (status == "done") {
                window.location.replace(`http://localhost:8000/static/${id}/output/index.html`)
                clearInterval(timer);
            }
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