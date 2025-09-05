const express=require('express')
const mongoose=require('mongoose')
require('dotenv').config()
const path=require('path')
const port=5000

const app=express()
app.use(express.static(__dirname))
app.use(express.json());
app.use(express.urlencoded({extended:true}))

mongoose.connect('mongodb://0.0.0.0:27017/vitmas')
const db =mongoose.connection
db.once('open',()=>{
    console.log('MongoDB connection successful')
})

const userSchema=new mongoose.Schema({
    fullname: String,
    regno: String,
    email: String,
    pwd: String,
    branch: String
})
const Users=mongoose.model("data",userSchema)

app.get('/',(req,res)=>{
    res.sendFile(path.join(__dirname, 'Homepage.html'));
})
app.post('/post',async (req,res)=>{
    const {fullname,regno,email,pwd,branch}=req.body
    const user=new Users({
        fullname,
        regno,
        email,
        pwd,
        branch
    })
    await user.save()
    console.log(user)
    res.send("Form submission succesful")
})

const authRoutes = require('./routes/auth');
app.use('/api/auth', authRoutes);
app.post('/api/auth/login', async (req, res) => {
  const { email, pwd } = req.body;
  console.log("Login request body:", req.body);  
  const user = await Users.findOne({ email });
  console.log("User found in DB:", user);
  if (!user || user.pwd !== pwd) {
    return res.status(400).json({ message: "Invalid email or password" });
  }
  console.log("Login successful for:", email);
  res.json({ message: "Login successful" });
});


app.listen(port,()=>{
    console.log("Server started")
})

