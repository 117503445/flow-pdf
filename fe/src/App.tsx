import './App.css'
import { useState } from 'react';

function App() {
  const [isDisabled, setIsDisabled] = useState(false);

  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    console.log('submit');
    event.preventDefault();

    const target = event.target as HTMLFormElement;

    // TODO prevent empty
    const formData = new FormData(target);

    if (formData.get('f') == null) {
      alert('Please select a file');
      return;
    }
    const f: File = formData.get('f') as File;
    if (f.size == 0) {
      alert('Please select a file');
      return;
    }
    if (f.size > 1024 * 1024 * 20) {
      alert('File size should be less than 20MB');
      return;
    }

    setIsDisabled(true)

    const response = await fetch(import.meta.env.VITE_BE_HOST + '/api/task', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    console.log(data);
    if (data['code'] != 0) {
      alert(data);
      setIsDisabled(false)
      return;
    }

    const taskID = data['data']['taskID'];
    const w = window.open('about:blank');
    if (w != null) {
      w.location.href = "/#/task/" + taskID;
    } else {
      alert('Please allow popups for this website');
    }

    setIsDisabled(false)
  }

  return (
    <>
      <h1>flow-pdf</h1>

      <p>flow-pdf converts PDFs into fluid and dynamic HTML documents, transforming the static layout of PDFs into a responsive and user-friendly format.</p>


      <form onSubmit={handleSubmit}>
        <input type="file" name="f" accept=".pdf" />
        <button type="submit" disabled={isDisabled}>提交</button>
      </form>

      <p>You can see more help on <a href='https://github.com/117503445/flow-pdf'>GitHub</a> (like how to translate)</p>
      <p>If it helps you, please give it a star :)</p>
    </>
  )
}

export default App
