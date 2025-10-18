import React, { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';
import "./Dealers.css";
import "../assets/style.css";
import Header from '../Header/Header';


const PostReview = () => {
  const [dealer, setDealer] = useState({});
  const [review, setReview] = useState("");
  const [make, setMake] = useState("");
  const [model, setModel] = useState("");
  const [year, setYear] = useState("");
  const [date, setDate] = useState("");
  const [carmodels, setCarmodels] = useState([]);

  let curr_url = window.location.href;
  let root_url = curr_url.substring(0,curr_url.indexOf("postreview"));
  let params = useParams();
  let id = params.id;
  let dealer_url = root_url+`djangoapp/dealer/${id}`;
  let review_url = root_url+`djangoapp/add_review`;
  let carmodels_url = root_url+`djangoapp/get_cars`;

  const postreview = async ()=>{
    let name = sessionStorage.getItem("firstname")+" "+sessionStorage.getItem("lastname");
    // If the first and second name are stored as null, use the username
    if(!name || name.includes("null")) {
      name = sessionStorage.getItem("username") || "Anonymous";
    }
    if(!model || review === "" || date === "" || year === "" ) {
      alert("All details are mandatory");
      return;
    }

    let model_split = model.split(" ");
    let make_chosen = model_split[0] || "";
    let model_chosen = model_split[1] || "";

    let jsoninput = JSON.stringify({
      "name": name,
      "dealership": id,
      "review": review,
      "purchase": true,
      "purchase_date": date,
      "car_make": make_chosen,
      "car_model": model_chosen,
      "car_year": year,
    });

    try {
      const res = await fetch(review_url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: jsoninput,
      });

      const json = await res.json();
      if (json.status === 200) {
        window.location.href = window.location.origin+"/dealer/"+id;
      } else {
        alert("Failed to post review. Please try again.");
      }
    } catch (err) {
      console.error(err);
      alert("Network error while posting review.");
    }
  }

  const get_dealer = async ()=>{
    const res = await fetch(dealer_url, { method: "GET" });
    const retobj = await res.json();
    if(retobj.status === 200) {
      let dealerobjs = Array.from(retobj.dealer)
      if(dealerobjs.length > 0)
        setDealer(dealerobjs[0])
    }
  }

  const get_cars = async ()=>{
    const res = await fetch(carmodels_url, { method: "GET" });
    const retobj = await res.json();
    let carmodelsarr = Array.from(retobj.CarModels || []);
    setCarmodels(carmodelsarr);
  }

  useEffect(() => {
    get_dealer();
    get_cars();
  },[]);

  const isSubmitDisabled = !model || !review || !date || !year;

  return (
    <div>
      <Header/>
      <div className="postreview_container" style={{maxWidth:800, margin:"2rem auto", padding:"1rem"}}>
        <h1 style={{color:"darkblue", marginBottom:8}}>{dealer.full_name || 'Dealer'}</h1>

        <label htmlFor="review" style={{display:'block', marginBottom:6}}>Your review</label>
        <textarea id='review' cols='60' rows='6' placeholder='Write your review here' value={review} onChange={(e) => setReview(e.target.value)} style={{width:'100%', padding:8, marginBottom:12}} />

        <div className='input_field' style={{marginBottom:12}}>
          <label style={{marginRight:8}}>Purchase Date</label>
          <input type="date" value={date} onChange={(e) => setDate(e.target.value)}/>
        </div>

        <div className='input_field' style={{marginBottom:12, display:'flex', gap:12, alignItems:'center'}}>
          <div style={{display:'flex', flexDirection:'column'}}>
            <label style={{marginBottom:6}}>Car Make</label>
            <select name="make" id="make" aria-label="Car Make" value={make} onChange={(e) => { setMake(e.target.value); setModel(""); }}>
              <option value="">Choose Make</option>
              {Array.from(new Set(carmodels.map(c => c.CarMake))).map((m, i) => (
                <option key={i} value={m}>{m}</option>
              ))}
            </select>
          </div>

          <div style={{display:'flex', flexDirection:'column', flex:1}}>
            <label style={{marginBottom:6}}>Car Model</label>
            <select name="model" id="model" aria-label="Car Model" value={model} onChange={(e) => setModel(e.target.value)}>
              <option value="">Choose Model</option>
              {carmodels.filter(c => !make || c.CarMake === make).map((carmodel, idx) => (
                <option key={idx} value={carmodel.CarMake+" "+carmodel.CarModel}>{carmodel.CarModel}</option>
              ))}
            </select>
          </div>
        </div>

        <div className='input_field' style={{marginBottom:16}}>
          <label style={{marginRight:8}}>Car Year</label>
          <input type="number" value={year} onChange={(e) => setYear(e.target.value)} max={2025} min={1900} />
        </div>

        <div>
          <button className='postreview' onClick={postreview} disabled={isSubmitDisabled} style={{padding:'8px 16px', cursor: isSubmitDisabled? 'not-allowed':'pointer'}}>Post Review</button>
        </div>
      </div>
    </div>
  )
}
export default PostReview
