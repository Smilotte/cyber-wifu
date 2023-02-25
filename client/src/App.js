import React from 'react';
import './App.css';
import Chatbox from "./pages/chatbox/Chatbox";
import {loadLive2DModel} from "oh-my-live2d";

/**
 * @author Smilotte
 * The page for App. Main domain.
 */
loadLive2DModel({
    sayHello: false,
    transitionTime: 2000,
    source: "build/assets/hiyori_pro_en/runtime/",
    models: {
        path: "hiyori_pro_t10.model3.json",
        stageStyle: {
            width: 'auto',
            height: 'auto'
        }
    },
    tips: false
});

class App extends React.Component {
    /**
     * The block for render and router. The main background is defined in App.css
     * @returns {*}
     */
    render() {
        return (
            <Chatbox/>
        )
    }
}

export default App;
