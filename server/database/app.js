const express = require('express');
const mongoose = require('mongoose');
const fs = require('fs');
const cors = require('cors');
const app = express();
const port = 3030;

app.use(cors());
app.use(require('body-parser').urlencoded({ extended: false }));

const path = require('path');
const reviews_data = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'reviews.json'), 'utf8'));
const dealerships_data = JSON.parse(fs.readFileSync(path.join(__dirname, 'data', 'dealerships.json'), 'utf8'));

// Try to connect to MongoDB; if unavailable, fall back to in-memory JSON data
let useMongo = false;
const mongoUri = process.env.MONGO_URI || 'mongodb://mongo_db:27017/';
mongoose.connect(mongoUri, { dbName: 'dealershipsDB', serverSelectionTimeoutMS: 5000 })
  .then(() => {
    useMongo = true;
    console.log('Connected to MongoDB, using DB-backed collections.');
  })
  .catch((err) => {
    useMongo = false;
    console.warn('Could not connect to MongoDB; falling back to JSON in-memory data. Error:', err.message);
  });

let Reviews = null;
let Dealerships = null;
if (useMongo) {
  Reviews = require('./review');
  Dealerships = require('./dealership');
  // populate DB (best-effort)
  try {
    Reviews.deleteMany({}).then(() => {
      Reviews.insertMany(reviews_data['reviews']);
    });
    Dealerships.deleteMany({}).then(() => {
      Dealerships.insertMany(dealerships_data['dealerships']);
    });
  } catch (error) {
    console.log(error);
  }
} else {
  // keep arrays in memory
  Reviews = reviews_data['reviews'];
  Dealerships = dealerships_data['dealerships'];
}

// Express route to home
app.get('/', async (req, res) => {
  res.send("Welcome to the Mongoose API");
});

// Express route to fetch all reviews
app.get('/fetchReviews', async (req, res) => {
  try {
    if (useMongo) {
      const documents = await Reviews.find();
      res.json(documents);
    } else {
      res.json(Reviews);
    }
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch reviews by a particular dealer
app.get('/fetchReviews/dealer/:id', async (req, res) => {
  try {
    if (useMongo) {
      const documents = await Reviews.find({ dealership: req.params.id });
      res.json(documents);
    } else {
      const documents = Reviews.filter(r => String(r.dealership) === String(req.params.id));
      res.json(documents);
    }
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch all dealerships
app.get('/fetchDealers', async (req, res) => {
  try {
    if (useMongo) {
      const documents = await Dealerships.find();
      res.json(documents);
    } else {
      res.json(Dealerships);
    }
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch Dealers by a particular state
app.get('/fetchDealers/:state', async (req, res) => {
  try {
    if (useMongo) {
      const documents = await Dealerships.find({ state: req.params.state });
      res.json(documents);
    } else {
      const documents = Dealerships.filter(d => String(d.state) === String(req.params.state));
      res.json(documents);
    }
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to fetch dealer by a particular id
app.get('/fetchDealer/:id', async (req, res) => {
  try {
    if (useMongo) {
      const documents = await Dealerships.find({ id: req.params.id });
      res.json(documents);
    } else {
      const documents = Dealerships.filter(d => String(d.id) === String(req.params.id));
      res.json(documents);
    }
  } catch (error) {
    res.status(500).json({ error: 'Error fetching documents' });
  }
});

// Express route to insert review
app.post('/insert_review', express.raw({ type: '*/*' }), async (req, res) => {
  try {
    const data = JSON.parse(req.body);
    if (useMongo) {
      const documents = await Reviews.find().sort({ id: -1 });
      let new_id = documents.length > 0 ? documents[0]['id'] + 1 : 1;

      const review = new Reviews({
        "id": new_id,
        "name": data['name'],
        "dealership": data['dealership'],
        "review": data['review'],
        "purchase": data['purchase'],
        "purchase_date": data['purchase_date'],
        "car_make": data['car_make'],
        "car_model": data['car_model'],
        "car_year": data['car_year'],
      });

      const savedReview = await review.save();
      res.json(savedReview);
    } else {
      const documents = Reviews;
      let new_id = documents.length > 0 ? Math.max(...documents.map(d=>d.id)) + 1 : 1;
      const reviewObj = {
        "id": new_id,
        "name": data['name'],
        "dealership": data['dealership'],
        "review": data['review'],
        "purchase": data['purchase'],
        "purchase_date": data['purchase_date'],
        "car_make": data['car_make'],
        "car_model": data['car_model'],
        "car_year": data['car_year'],
      };
      Reviews.push(reviewObj);
      res.json(reviewObj);
    }
  } catch (error) {
    console.log(error);
    res.status(500).json({ error: 'Error inserting review' });
  }
});

// Start the Express server
app.listen(port, () => {
  console.log(`Server is running on http://localhost:${port}`);
});