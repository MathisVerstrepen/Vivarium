import { Scene } from 'phaser';

export class MainScene extends Scene {
    constructor() {
        super({ key: 'MainScene' });
    }

    preload() {
        // Load assets here (place images in your /public folder)
        // this.load.image('logo', '/logo.png');
    }

    create() {
        // Create game objects
        const text = this.add.text(400, 300, 'AI Playground Active', {
            fontSize: '32px',
            color: '#ffffff',
        });
        text.setOrigin(0.5);

        // Example: Draw a grid for your AI world
        const graphics = this.add.graphics();
        graphics.lineStyle(1, 0x00ff00, 0.5);
        for (let x = 0; x < 800; x += 32) {
            graphics.moveTo(x, 0);
            graphics.lineTo(x, 600);
        }
        for (let y = 0; y < 600; y += 32) {
            graphics.moveTo(0, y);
            graphics.lineTo(800, y);
        }
        graphics.strokePath();
    }

    update() {
        // The game loop (runs ~60 times per second)
    }
}
