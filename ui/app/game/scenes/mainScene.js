import Phaser, { Scene, Math as PhaserMath } from 'phaser';

export class MainScene extends Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.player = null;
        this.cursors = null;
        this.isFreeCam = false;
    }

    preload() {
        // 1. Load the Tileset Image
        this.load.image('Room_Builder_48x48', '/tilesets/Interiors/Room_Builder_48x48.png');
        this.load.image('Interiors_48x48_1', '/tilesets/Interiors/Interiors_48x48_1.png');
        this.load.image('Interiors_48x48_2', '/tilesets/Interiors/Interiors_48x48_2.png');
        this.load.image('Exteriors', '/tilesets/Exteriors/Exteriors.png');
        this.load.image('collisions', '/tilesets/collisions.png');

        // 2. Load the Tiled JSON
        this.load.tilemapTiledJSON('map-key', '/maps/world.json');

        // 3. Load Player Sprite
        this.load.image('player', '/sprites/player.png');
    }

    create() {
        // 1. Create the map object
        const map = this.make.tilemap({ key: 'map-key' });

        // 2. Add the tileset to the map
        const tilesetRoomBuilder = map.addTilesetImage('Room_Builder_48x48', 'Room_Builder_48x48');
        const tilesetInteriors1 = map.addTilesetImage('Interiors_48x48_1', 'Interiors_48x48_1');
        const tilesetInteriors2 = map.addTilesetImage('Interiors_48x48_2', 'Interiors_48x48_2');
        const tilesetExteriors = map.addTilesetImage('Exteriors', 'Exteriors');
        const tilesetCollisions = map.addTilesetImage('collisions', 'collisions');
        const tilesets = [
            tilesetRoomBuilder,
            tilesetInteriors1,
            tilesetInteriors2,
            tilesetExteriors,
        ];

        // 3. Create Layers
        map.createLayer('Ground', tilesets, 0, 0);
        map.createLayer('Base', tilesets, 0, 0);
        map.createLayer('Objects', tilesets, 0, 0);
        const collisionsLayer = map.createLayer('Collisions', tilesetCollisions, 0, 0);

        // 4. Create Player
        const spawnX = map.widthInPixels / 2;
        const spawnY = map.heightInPixels / 2;

        this.player = this.physics.add.sprite(spawnX, spawnY, 'player');
        this.player.setDepth(10);

        // 5. Set collisions
        collisionsLayer.setCollisionByExclusion([-1]);
        collisionsLayer.setVisible(false);

        this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.player.setCollideWorldBounds(true);

        this.physics.add.collider(this.player, collisionsLayer);

        // 6. Camera Setup
        this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.cameras.main.startFollow(this.player, true, 0.1, 0.1);

        // 7. Input Events: Zoom
        this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY) => {
            const zoomDirection = deltaY > 0 ? -1 : 1;
            const zoomStep = 0.1;

            const newZoom = this.cameras.main.zoom + zoomDirection * zoomStep;

            this.cameras.main.zoom = PhaserMath.Clamp(newZoom, 0.5, 3);
        });

        // 8. Initialize Keyboard Controls
        this.cursors = this.input.keyboard.createCursorKeys();

        this.wasd = this.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.Z,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.Q,
            right: Phaser.Input.Keyboard.KeyCodes.D,
        });

        // 9. Event Listeners (UI Bridge)
        this.handleFreeCamToggle = () => {
            this.isFreeCam = !this.isFreeCam;
            if (this.isFreeCam) {
                this.cameras.main.stopFollow();
                this.player.setVelocity(0);
            } else {
                this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
            }
        };

        window.addEventListener('vivarium-toggle-free-cam', this.handleFreeCamToggle);

        // Cleanup listener on scene shutdown
        this.events.on('shutdown', () => {
            window.removeEventListener('vivarium-toggle-free-cam', this.handleFreeCamToggle);
        });
    }

    update() {
        if (!this.player || !this.cursors) return;

        if (this.isFreeCam) {
            // --- Free Cam Logic ---
            const cameraSpeed = 10; // Pixels per frame (approx)
            // Adjust speed based on zoom so it doesn't feel too fast when zoomed in
            const adjustedSpeed = cameraSpeed / this.cameras.main.zoom;

            if (this.cursors.left.isDown || this.wasd.left.isDown) {
                this.cameras.main.scrollX -= adjustedSpeed;
            } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
                this.cameras.main.scrollX += adjustedSpeed;
            }

            if (this.cursors.up.isDown || this.wasd.up.isDown) {
                this.cameras.main.scrollY -= adjustedSpeed;
            } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
                this.cameras.main.scrollY += adjustedSpeed;
            }
        } else {
            // --- Player Movement Logic ---
            const speed = 200;
            this.player.setVelocity(0);

            // Horizontal Movement
            if (this.cursors.left.isDown || this.wasd.left.isDown) {
                this.player.setVelocityX(-speed);
            } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
                this.player.setVelocityX(speed);
            }

            // Vertical Movement
            if (this.cursors.up.isDown || this.wasd.up.isDown) {
                this.player.setVelocityY(-speed);
            } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
                this.player.setVelocityY(speed);
            }

            if (this.player.body.velocity.x !== 0 || this.player.body.velocity.y !== 0) {
                this.player.body.velocity.normalize().scale(speed);
            }
        }
    }
}
