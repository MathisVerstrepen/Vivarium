import Phaser, { Scene, Math as PhaserMath } from 'phaser';

export class MainScene extends Scene {
    constructor() {
        super({ key: 'MainScene' });
        this.player = null;
        this.cursors = null;
        this.isFreeCam = false;
        this.worldId = null;
        this.agentsGroup = null;
        this.agentMap = new Map();
    }

    init(data) {
        this.worldId = data.worldId;
        console.log(`Initializing World ID: ${this.worldId}`);
    }

    preload() {
        // 1. Load the Tileset Image
        this.load.image('Room_Builder_48x48', '/tilesets/Interiors/Room_Builder_48x48.png');
        this.load.image('Interiors_48x48_1', '/tilesets/Interiors/Interiors_48x48_1.png');
        this.load.image('Interiors_48x48_2', '/tilesets/Interiors/Interiors_48x48_2.png');
        this.load.image('Exteriors', '/tilesets/Exteriors/Exteriors.png');
        this.load.image('collisions', '/tilesets/collisions.png');
        this.load.tilemapTiledJSON('map-key', '/maps/world.json');
        this.load.spritesheet('player', '/sprites/player.png', {
            frameWidth: 48,
            frameHeight: 96,
        });
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
        map.createLayer('Objects 2', tilesets, 0, 0);
        map.createLayer('Objects 3', tilesets, 0, 0);
        const collisionsLayer = map.createLayer('Collisions', tilesetCollisions, 0, 0);

        // 4. Create Player
        const storageKeyX = `vivarium_pos_x_${this.worldId}`;
        const storageKeyY = `vivarium_pos_y_${this.worldId}`;
        const storedX = localStorage.getItem(storageKeyX);
        const storedY = localStorage.getItem(storageKeyY);
        let spawnX = storedX ? parseFloat(storedX) : map.widthInPixels / 2;
        let spawnY = storedY ? parseFloat(storedY) : map.heightInPixels / 2;

        this.player = this.physics.add.sprite(spawnX, spawnY, 'player');
        this.player.setDepth(10);
        this.player.body.setSize(44, 44);
        this.player.body.setOffset(2, 46);

        // 5. Create Agent Group
        this.agentsGroup = this.physics.add.group();
        this.physics.add.collider(this.agentsGroup, collisionsLayer);
        this.physics.add.collider(this.player, this.agentsGroup);

        // --- Define Animations ---
        // Grid has 56 columns and 20 rows

        this.anims.create({
            key: 'down',
            frames: this.anims.generateFrameNumbers('player', {
                frames: [130, 131, 132, 133, 134, 135],
            }),
            frameRate: 10,
            repeat: -1,
        });
        this.anims.create({
            key: 'left',
            frames: this.anims.generateFrameNumbers('player', {
                frames: [124, 125, 126, 127, 128, 129],
            }),
            frameRate: 10,
            repeat: -1,
        });
        this.anims.create({
            key: 'right',
            frames: this.anims.generateFrameNumbers('player', {
                frames: [112, 113, 114, 115, 116, 117],
            }),
            frameRate: 12,
            repeat: -1,
        });
        this.anims.create({
            key: 'up',
            frames: this.anims.generateFrameNumbers('player', {
                frames: [118, 119, 120, 121, 122, 123],
            }),
            frameRate: 10,
            repeat: -1,
        });

        collisionsLayer.setCollisionByExclusion([-1]);
        collisionsLayer.setVisible(false);
        this.physics.world.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.player.setCollideWorldBounds(true);
        this.physics.add.collider(this.player, collisionsLayer);

        this.cameras.main.setBounds(0, 0, map.widthInPixels, map.heightInPixels);
        this.cameras.main.startFollow(this.player, true, 0.1, 0.1);

        // --- INPUT SETUP ---
        this.input.on('wheel', (pointer, gameObjects, deltaX, deltaY) => {
            const zoomDirection = deltaY > 0 ? -1 : 1;
            const newZoom = PhaserMath.Clamp(this.cameras.main.zoom + zoomDirection * 0.1, 0.5, 3);
            this.cameras.main.zoom = newZoom;
        });

        this.cursors = this.input.keyboard.createCursorKeys();
        this.wasd = this.input.keyboard.addKeys({
            up: Phaser.Input.Keyboard.KeyCodes.Z,
            down: Phaser.Input.Keyboard.KeyCodes.S,
            left: Phaser.Input.Keyboard.KeyCodes.Q,
            right: Phaser.Input.Keyboard.KeyCodes.D,
            shift: Phaser.Input.Keyboard.KeyCodes.SHIFT,
        });

        // --- EVENT LISTENERS ---

        // 1. Free Cam Toggle
        this.handleFreeCamToggle = () => {
            this.isFreeCam = !this.isFreeCam;
            if (this.isFreeCam) {
                this.cameras.main.stopFollow();
                this.player.setVelocity(0);
            } else {
                this.cameras.main.startFollow(this.player, true, 0.1, 0.1);
            }
        };

        // 2. Input Capture
        this.handleInputCapture = (e) => {
            const shouldCapture = e.detail;
            this.input.keyboard.enabled = !shouldCapture;
            if (shouldCapture && this.player && this.player.body) {
                this.player.setVelocity(0);
                this.player.anims.stop();
            }
        };

        // 3. Handle Agent Spawn Event (from Vue)
        this.handleAgentSpawn = (e) => {
            const agentData = e.detail;
            this.spawnAgent(agentData);
        };

        window.addEventListener('vivarium-toggle-free-cam', this.handleFreeCamToggle);
        window.addEventListener('vivarium-input-capture', this.handleInputCapture);
        window.addEventListener('vivarium-agent-spawned', this.handleAgentSpawn);

        this.events.on('shutdown', () => {
            window.removeEventListener('vivarium-toggle-free-cam', this.handleFreeCamToggle);
            window.removeEventListener('vivarium-input-capture', this.handleInputCapture);
            window.removeEventListener('vivarium-agent-spawned', this.handleAgentSpawn);
        });

        this.time.addEvent({
            delay: 1000,
            loop: true,
            callback: () => {
                if (this.player && this.worldId) {
                    localStorage.setItem(`vivarium_pos_x_${this.worldId}`, this.player.x);
                    localStorage.setItem(`vivarium_pos_y_${this.worldId}`, this.player.y);
                }
            },
        });

        // --- INITIAL AGENT LOAD ---
        this.loadAgents();
    }

    async loadAgents() {
        try {
            const response = await fetch(`http://127.0.0.1:8000/worlds/${this.worldId}/agents`);
            const agents = await response.json();
            agents.forEach((agent) => this.spawnAgent(agent));
        } catch (e) {
            console.error('Failed to load initial agents', e);
        }
    }

    spawnAgent(agent) {
        if (this.agentMap.has(agent.id)) return;

        const x = agent.x || 400;
        const y = agent.y || 400;

        const sprite = this.agentsGroup.create(x, y, 'player');
        sprite.setDepth(9);
        sprite.body.setSize(44, 44);
        sprite.body.setOffset(2, 46);
        sprite.setImmovable(true);
        sprite.setTint(0xffaaaa);
        sprite.setFrame(3);

        // Add label
        const label = this.add
            .text(x, y - 50, agent.name, {
                font: '12px Arial',
                fill: '#ffffff',
                stroke: '#000000',
                strokeThickness: 3,
            })
            .setOrigin(0.5);

        sprite.label = label;
        this.agentMap.set(agent.id, sprite);
    }

    update() {
        this.agentMap.forEach((sprite) => {
            if (sprite.label) {
                sprite.label.setPosition(sprite.x, sprite.y - 50);
            }
        });

        if (!this.player || !this.cursors) return;

        // If keyboard is disabled (UI is open), stop update logic
        if (!this.input.keyboard.enabled) return;

        if (this.isFreeCam) {
            const cameraSpeed = 10;
            const adjustedSpeed = cameraSpeed / this.cameras.main.zoom;

            if (this.cursors.left.isDown || this.wasd.left.isDown)
                this.cameras.main.scrollX -= adjustedSpeed;
            else if (this.cursors.right.isDown || this.wasd.right.isDown)
                this.cameras.main.scrollX += adjustedSpeed;

            if (this.cursors.up.isDown || this.wasd.up.isDown)
                this.cameras.main.scrollY -= adjustedSpeed;
            else if (this.cursors.down.isDown || this.wasd.down.isDown)
                this.cameras.main.scrollY += adjustedSpeed;
        } else {
            const baseSpeed = 200;
            const sprintSpeed = 350;
            const isSprinting = this.cursors.shift.isDown || this.wasd.shift.isDown;
            const speed = isSprinting ? sprintSpeed : baseSpeed;

            this.player.setVelocity(0);

            if (this.cursors.left.isDown || this.wasd.left.isDown) {
                this.player.setVelocityX(-speed);
                this.player.anims.play('left', true);
            } else if (this.cursors.right.isDown || this.wasd.right.isDown) {
                this.player.setVelocityX(speed);
                this.player.anims.play('right', true);
            }

            if (this.cursors.up.isDown || this.wasd.up.isDown) {
                this.player.setVelocityY(-speed);
                this.player.anims.play('up', true);
            } else if (this.cursors.down.isDown || this.wasd.down.isDown) {
                this.player.setVelocityY(speed);
                this.player.anims.play('down', true);
            }

            if (this.player.body.velocity.x !== 0 || this.player.body.velocity.y !== 0) {
                this.player.body.velocity.normalize().scale(speed);
            } else {
                this.player.anims.stop();
                this.player.setFrame(3);
            }
        }
    }
}
