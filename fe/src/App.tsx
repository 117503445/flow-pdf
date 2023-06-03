import './App.css'

function App() {
  async function handleSubmit(event: React.FormEvent<HTMLFormElement>) {
    console.log('submit');
    event.preventDefault();

    const target = event.target as HTMLFormElement;

    // TODO prevent empty
    const formData = new FormData(target);

    // TODO Read Config
    const response = await fetch(import.meta.env.VITE_BE_HOST + '/api/task', {
      method: 'POST',
      body: formData
    });
    const data = await response.json();
    console.log(data);

    const taskID = data['data']['taskID'];
    const w = window.open('about:blank');
    if (w != null) {
      w.location.href = "/#/task/" + taskID;
    } else {
      alert('Please allow popups for this website');
    }

  }

  return (
    <>
      <h1>flow-pdf</h1>

      <p>flow-pdf converts PDFs into fluid and dynamic HTML documents, transforming the static layout of PDFs into a responsive and user-friendly format.</p>


      <form onSubmit={handleSubmit}>
        <input type="file" name="f" accept=".pdf" />
        <button type="submit">提交</button>
      </form>
    </>
  )
}

export default App
