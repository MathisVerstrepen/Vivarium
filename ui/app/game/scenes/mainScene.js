import { Scene } from 'phaser';

export class MainScene extends Scene {
    constructor() {
        super({ key: 'MainScene' });
    }

    preload() {
        // 1. Load the Tileset Image
        this.load.image('Room_Builder_48x48', '/tilesets/Interiors/Room_Builder_48x48.png');
        this.load.image('Interiors_48x48_1', '/tilesets/Interiors/Interiors_48x48_1.png');
        this.load.image('Interiors_48x48_2', '/tilesets/Interiors/Interiors_48x48_2.png');
        this.load.image('Exteriors', '/tilesets/Exteriors/Exteriors.png');

        // 2. Load the Tiled JSON
        this.load.tilemapTiledJSON('map-key', '/maps/world.json');
    }

    create() {
        // 1. Create the map object
        const map = this.make.tilemap({ key: 'map-key' });

        // 2. Add the tileset to the map
        const tilesetRoomBuilder = map.addTilesetImage('Room_Builder_48x48', 'Room_Builder_48x48');
        const tilesetInteriors1 = map.addTilesetImage('Interiors_48x48_1', 'Interiors_48x48_1');
        const tilesetInteriors2 = map.addTilesetImage('Interiors_48x48_2', 'Interiors_48x48_2');
        const tilesetExteriors = map.addTilesetImage('Exteriors', 'Exteriors');
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
        const charactersLayer = map.createLayer('Characters', tilesets, 0, 0);
        const collisionsLayer = map.createLayer('Collisions', [], 0, 0);

        // 4. Set collisions for the AI
        collisionsLayer.setCollisionByProperty({ collides: true });
    }
}
