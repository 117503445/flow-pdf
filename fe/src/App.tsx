import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)


  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    console.log('submit');
    event.preventDefault();

    const target = event.target as HTMLFormElement;

    const formData = new FormData(target);
    const response = await fetch('http://localhost:8000/api/task', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    console.log(data);
  }

  return (
    <>
      <h1>flow-pdf</h1>

      <p>flow-pdf converts PDFs into fluid and dynamic HTML documents, transforming the static layout of PDFs into a responsive and user-friendly format.</p>


      <form onSubmit={handleSubmit}>
        <input type="file" name="file" accept=".pdf" />
        <button type="submit">提交</button>
      </form>
    </>
  )
}

export default App
