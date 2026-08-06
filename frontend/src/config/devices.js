export const devices = [

    {
        id: "esp32_main",

        name: "Hydroponics Controller",

        controls: [

            { name: "Pump A", relay: 33 },

            { name: "Pump B", relay: 25 },

            { name: "Pump C", relay: 26 }

        ]
    },

    {
        id: "esp32_incubator",

        name: "Seed Incubator",

        controls: [

            { name: "Lights", relay: 26 },

            { name: "Fan", relay: 27 },

            { name: "Heater", relay: 14 }

        ]
    }

];