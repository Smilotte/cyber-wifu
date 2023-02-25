import React from 'react';
import "./Chatbox.css"
import axios from "axios";

/**
 * @author Smilotte
 * The page for Home. Main home page
 */
class Chatbox extends React.Component {

    constructor(props) {
        super(props);
        this.submit = this.submit.bind(this);
    }

    // On form submit, send message
    submit(e) {
        e.preventDefault();

        const chatWindowMessage = document.querySelector('.chat-window-message');
        console.log(chatWindowMessage.value)

        const message = chatWindowMessage.value;
        if (message !== "") {
            this.handleMessage(message);
            this.handleReply(message);
            // this.sendMessage(message);
            // this.handleText();
        }

    };

    getVoice(message) {
        axios.get('http://127.0.0.1:5000/audio', {
            // axios.get('http://cyberwifu.vipgz4.91tunnel.com/audio', {
            responseType: "arraybuffer",
            params: {text: message}
        })
            .then((data) => {
                const context = new (window.AudioContext || window.webkitAudioContext)();
                context.decodeAudioData(data.data, function (buffer) {
                    const source = context.createBufferSource();
                    source.buffer = buffer;
                    source.connect(context.destination);
                    // auto play
                    source.start(0);
                });
            })
            .catch(error => console.log(error));
    }


    handleMessage(message) {
        const chatThread = document.querySelector('.chat-thread');
        const chatWindowMessage = document.querySelector('.chat-window-message');

        const chatNewThread = document.createElement("li");
        chatNewThread.className = "senderMsg"
        const chatNewMessage = document.createTextNode(message);

        // Add message to chat thread and scroll to bottom
        chatNewThread.appendChild(chatNewMessage);
        chatThread.appendChild(chatNewThread);
        chatThread.scrollTop = chatThread.scrollHeight;

        // Clear text value
        chatWindowMessage.value = '';
    }


    handleReply(message) {
        axios.get('http://127.0.0.1:8080/chat', {
            // axios.get('http://cyberwifu.vipgz4.91tunnel.com/chat', {
            responseType: "text",
            params: {text: message}
        })
            .then((data) => {
                console.log(data.data);
                const reply = data.data
                if (reply !== "") {
                    // this.getVoice(reply);
                    const chatThread = document.querySelector('.chat-thread');
                    const chatNewThread = document.createElement("li");
                    chatNewThread.className = "receiverMsg"
                    const chatNewMessage = document.createTextNode(reply);

                    // Add message to chat thread and scroll to bottom
                    chatNewThread.appendChild(chatNewMessage);
                    chatThread.appendChild(chatNewThread);
                    chatThread.scrollTop = chatThread.scrollHeight;
                }
            })
            .catch(error => console.log(error));
    }

    /**
     * render
     * @returns {*}
     */
    render() {
        return (
            <div className="chat-box">
                <ul className="chat-thread"/>

                <form className="chat-window" onSubmit={this.submit}>
                    <input className="chat-window-message" name="chat-window-message" type="text" autoComplete="off"
                           autoFocus/>
                </form>
            </div>
        )
    }
}

export default Chatbox;