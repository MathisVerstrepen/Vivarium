// --- Sub-components of Agent Profile ---

export interface Identity {
    name: string;
    age: number;
    gender: string;
    occupation: string;
    backstory: string;
}

export interface Psychology {
    openness: number;
    conscientiousness: number;
    extraversion: number;
    agreeableness: number;
    neuroticism: number;
}

export interface MoralCompass {
    care_harm: number;
    fairness_cheating: number;
    loyalty_betrayal: number;
    authority_subversion: number;
    sanctity_degradation: number;
}

export interface EmotionalProfile {
    base_mood: string;
    emotional_volatility: number;
    attachment_style: 'Secure' | 'Anxious-Preoccupied' | 'Dismissive-Avoidant' | 'Fearful-Avoidant';
    triggers: string[];
}

export interface Cognition {
    decision_basis: 'Logic' | 'Emotion' | 'Intuition' | 'Tradition';
    impulsivity: number;
}

export interface CommunicationStyle {
    verbosity: number;
    formality: number;
    tone: string;
}

export interface AgentProfile {
    identity: Identity;
    psychology: Psychology;
    morality: MoralCompass;
    emotions: EmotionalProfile;
    cognition: Cognition;
    communication: CommunicationStyle;
}

// --- API DTOs ---

export interface World {
    id: number;
    name: string;
}

export interface CreateWorldRequest {
    name: string;
}

export interface Agent {
    id: number;
    world_id: number;
    name: string;
    current_situation: string;
    x: number;
    y: number;
}

export interface AgentDetail extends Agent {
    profile: AgentProfile;
    short_term_memory: string[];
    mid_term_memory: string[];
}

export interface CreateAgentRequest {
    world_id: number;
    profile: AgentProfile;
    initial_situation?: string;
    x?: number;
    y?: number;
}

export interface AgentOutput {
    inner_monologue: string;
    mood: string;
    speech: string;
    end_conversation: boolean;
}

export interface InteractionResponse {
    source_agent_id: number;
    target_agent_id: number;
    source_agent_name: string;
    output: AgentOutput;
    memory_compressed: boolean;
}

export interface WhisperRequest {
    agent_id: number;
    content: string;
}

export interface ChatResponse {
    agent_id: number;
    agent_name: string;
    response: AgentOutput;
}

export interface ChatResponse {
    agent_id: number;
    agent_name: string;
    response: AgentOutput;
}

export interface EndChatResponse {
    agent_id: number;
    memories_created: string[];
}
