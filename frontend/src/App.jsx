import React, { useContext } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  Navigate,
} from "react-router-dom";
import Home from "./pages/Home";
import Loader from "./components/Loader";
import Navbar from "./components/Navbar";

const App = () => {

  return (
    <div className="flex flex-col min-h-screen md:h-screen p-4 md:p-8 text-primary">
      <Router>
        <Navbar />
        <Routes>
          <Route path="*" element={<Navigate to="/" />} />
          <Route path="/" element={<Home />} />
          <Route
            path="/payment-status/:txnid"
            element={
              // true ? <PaymentStatus /> : <Navigate to="/" />
              <Loader />
            }
          />
        </Routes>
      </Router>
    </div>
  );
};

export default App;
