import React, { useState } from 'react';  
import axios from 'axios';  
  
interface Message {  
  id: number;  
  text: string;  
  sender: 'user' | 'bot';  
  imageUrl?: string;  
}  
  
const Chat: React.FC = () => {  
  const [messages, setMessages] = useState<Message[]>([]);  
  const [input, setInput] = useState<string>('');  
  const [selectedFile, setSelectedFile] = useState<File | null>(null);  
  const [imagePreviewUrl, setImagePreviewUrl] = useState<string | null>(null);  
  
  const sendMessage = async () => {  
    if (input.trim() === '' && !selectedFile) return;  
  
    const userMessage: Message = {  
      id: Date.now(),  
      text: input,  
      sender: 'user',  
      imageUrl: imagePreviewUrl || undefined,  
    };  
  
    setMessages([...messages, userMessage]);  
  
    // Prepare the payload  
    const payload: any = {  
      messages: [  
        { role: 'system', content: [{ type: 'text', text: 'You are an AI assistant that helps people find information.' }] },  
        { role: 'user', content: [{ type: 'text', text: input }] }  
      ],  
      temperature: 0.7,  
      top_p: 0.95,  
      frequency_penalty: 0,  
      max_tokens: 2000,  
      presence_penalty: 0,  
      stop: null,  
      stream: false  
    };  
  
    if (selectedFile) {  
      const reader = new FileReader();  
      reader.onloadend = async () => {  
        const base64String = reader.result!.toString().split(',')[1];  
        payload.messages.push({  
          role: 'user',  
          content: [{ type: 'image_url', image_url: { url: `data:image/png;base64,${base64String}` } }]  
        });  
  
        try {  
          const response = await axios.post('http://localhost:5000/api/chat', payload, {  
            headers: {  
              'Content-Type': 'application/json',  
            },  
          });  
  
          const botMessage: Message = {  
            id: Date.now() + 1,  
            text: response.data,  
            sender: 'bot',  
          };  
  
          setMessages([...messages, userMessage, botMessage]);  
          setSelectedFile(null);  
          setImagePreviewUrl(null);  
        } catch (error) {  
          console.error('Error sending message:', error);  
        }  
      };  
      reader.readAsDataURL(selectedFile);  
    } else {  
      try {  
        const response = await axios.post('http://localhost:5000/api/chat', payload, {  
          headers: {  
            'Content-Type': 'application/json',  
          },  
        });  
  
        const botMessage: Message = {  
          id: Date.now() + 1,  
          text: response.data,  
          sender: 'bot',  
        };  
  
        setMessages([...messages, userMessage, botMessage]);  
      } catch (error) {  
        console.error('Error sending message:', error);  
      }  
    }  
  
    setInput('');  
  };  
  
  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {  
    if (event.target.files && event.target.files[0]) {  
      const file = event.target.files[0];  
      setSelectedFile(file);  
      const reader = new FileReader();  
      reader.onloadend = () => {  
        setImagePreviewUrl(reader.result as string);  
      };  
      reader.readAsDataURL(file);  
    }  
  };  
  
  return (  
    <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', backgroundColor: '#f0f0f0' }}>  
      <div style={{ width: '800px', maxWidth: '100%', background: 'white', borderRadius: '8px', boxShadow: '0 0 10px rgba(0, 0, 0, 0.1)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>  
        <div style={{ flex: 1, padding: '20px', overflowY: 'auto', maxHeight: '1100px' }}>  
           
          {imagePreviewUrl && (  
            <div style={{ textAlign: 'right', marginBottom: '10px', padding: '10px', borderRadius: '4px', backgroundColor: '#daf8cb', alignSelf: 'flex-end' }}>  
              <img src={imagePreviewUrl} alt="preview" style={{ maxWidth: '300px', borderRadius: '4px' }} />  
            </div>  
          )}  
          {messages.map(msg => (  
            <div key={msg.id} style={{ textAlign: msg.sender === 'user' ? 'right' : 'left', marginBottom: '10px', padding: '10px', borderRadius: '4px', backgroundColor: msg.sender === 'user' ? '#daf8cb' : '#f1f1f1', alignSelf: msg.sender === 'user' ? 'flex-end' : 'flex-start' }}>  
              {msg.text && <p>{msg.text}</p>}  
              {msg.imageUrl && <img src={msg.imageUrl} alt="uploaded" style={{ maxWidth: '300px', borderRadius: '4px' }} />}  
            </div>  
          ))} 
        </div>  
        <div style={{ display: 'flex', borderTop: '1px solid #eee', padding: '10px' }}>  
          <input  
            type="text"  
            value={input}  
            onChange={e => setInput(e.target.value)}  
            onKeyPress={e => e.key === 'Enter' && sendMessage()}  
            style={{ flex: 1, padding: '10px', border: '1px solid #ccc', borderRadius: '4px', marginRight: '10px' }}  
            placeholder="Type a message..."  
          />  
          <input  
            type="file"  
            onChange={handleFileChange}  
            style={{ display: 'none' }}  
            id="fileInput"  
          />  
          <label htmlFor="fileInput" style={{ padding: '10px 20px', border: '1px solid #ccc', borderRadius: '4px', cursor: 'pointer', marginRight: '10px' }}>  
            Upload  
          </label>  
          <button onClick={sendMessage} style={{ padding: '10px 20px', border: 'none', backgroundColor: '#4caf50', color: 'white', borderRadius: '4px', cursor: 'pointer' }}>  
            Send  
          </button>  
        </div>  
      </div>  
    </div>  
  );  
};  
  
export default Chat;  
