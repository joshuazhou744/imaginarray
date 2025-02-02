// manipulationTypes.ts

export interface AppendManipulation<T> {
    type: 'append';
    value: T;
}

export interface SwapManipulation {
    type: 'swap';
    indices: [number, number];
}

export interface PopManipulation {
    type: 'pop';
}

export interface ReverseManipulation {
    type: 'reverse';
}

export interface ReplaceManipulation<T> {
    type: 'replace';
    index: number;
    value: T;
}

export interface ClearManipulation {
    type: 'clear';
}

export interface RemoveManipulation<T> {
    type: 'remove';
    value: T;
}

export interface DeleteManipulation {
    type: 'delete';
    index: number;
}

export interface VariableManipulation<T> {
    type: 'variable';
    name: string;
    value: T;
}


export type Manipulation<T> = 
    | AppendManipulation<T>
    | PopManipulation
    | ReverseManipulation
    | SwapManipulation
    | ReplaceManipulation<T>
    | ClearManipulation
    | RemoveManipulation<T>
    | DeleteManipulation
    | VariableManipulation<T>;