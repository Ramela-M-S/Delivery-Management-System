import { useContext, useState } from 'react'
import './App.css'
import { type Shipment, Card } from './Card'
import { UserContext } from './UserContext'

function App() {

  const { username, login, logout  } = useContext(UserContext)

  const [shipments, setShipments] = useState<Shipment[]>([])

  function addShipment(data: FormData) {
    const id = data.get("id")?.toString()

    if (!id) {
      return
    }

    setShipments([
      ...shipments,
      { id, status: "Placed" }
    ])
  }

  return (
    <>
      <div className="card">
        <h2>Hi {username},</h2>

        {
          username 
          ? <button onClick={logout}>Logout</button> 
          : <button onClick={() => login("RainForest")}>Login</button>
        }
        
      </div>

      {
        username &&
        <>
          <form action={addShipment}>
            <input type="text" name="id" placeholder="shipment id" required />
            <button type="submit">Submit</button>
          </form>

          <h1>Shipments:</h1>
          {
            shipments.map((shipment) => (
              <Card shipment={shipment} key={shipment.id} />
            ))
          }
        </>
      }

    </>
  )
}

export default App
