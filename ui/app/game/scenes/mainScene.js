import { Scene, Math as PhaserMath } from 'phaser';

export class MainScene extends Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.player = null;
        this.cursors = null;
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
        // Ensure you have a file at this path, or Phaser will render a green placeholder box.
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
        const groundLayer = map.createLayer('Ground', tilesets, 0, 0);
        const baseLayer = map.createLayer('Base', tilesets, 0, 0);
        const objectsLayer = map.createLayer('Objects', tilesets, 0, 0);
        const collisionsLayer = map.createLayer('Collisions', tilesetCollisions, 0, 0);

        // 4. Create Player
        // Spawning in the center of the map for now.
        const spawnX = map.widthInPixels / 2;
        const spawnY = map.heightInPixels / 2;

        this.player = this.physics.add.sprite(spawnX, spawnY, 'player');
        this.player.setDepth(10);

        // 5. Set collisions
        collisionsLayer.setCollisionByProperty({ collides: true });
        collisionsLayer.setVisible(false);

        this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.player.setCollideWorldBounds(true);

        this.physics.add.collider(this.player, collisionsLayer);

        // 6. Camera Setup
        this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);

        // Camera follows the player
        this.cameras.main.startFollow(this.player, true, 0.1, 0.1);

        // 7. Input Events: Zoom
        this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY, deltaZ) => {
            const zoomDirection = deltaY > 0 ? -1 : 1;
            const zoomStep = 0.1;

            const newZoom = this.cameras.main.zoom + zoomDirection * zoomStep;

            this.cameras.main.zoom = PhaserMath.Clamp(newZoom, 0.5, 3);
        });

        // 8. Initialize Keyboard Controls
        this.cursors = this.input.keyboard.createCursorKeys();

        // If you want WASD as well:
        this.wasd = this.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.Z,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.Q,
            right: Phaser.Input.Keyboard.KeyCodes.D,
        });
    }

    update() {
        if (!this.player || !this.cursors) return;

        const speed = 200; // Movement speed
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

        // Normalize and scale velocity so that diagonal movement isn't faster
        this.player.body.velocity.normalize().scale(speed);
    }
}
