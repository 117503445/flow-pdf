import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App.tsx'
import Task from './Task.tsx'
import './index.css'


import {
  RouterProvider,
  createHashRouter,
} from "react-router-dom";

console.log("VITE_BE_HOST", import.meta.env.VITE_BE_HOST);
console.log("VITE_STATIC_HOST", import.meta.env.VITE_STATIC_HOST)


const router = createHashRouter([
  {
    path: "/",
    element: <App />,
  }, {
    path: "/index.html",
    element: <App />,
  },
  {
    path: "/task/:id",
    element: <Task />,
  },
]);

ReactDOM.createRoot(document.getElementById('root') as HTMLElement).render(
  <React.StrictMode>
    <RouterProvider router={router} />
  </React.StrictMode>,
)
