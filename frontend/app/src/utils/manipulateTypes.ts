// manipulationTypes.ts

export interface AppendManipulation<T> {
    type: 'append';
    value: T;
}

export interface PopManipulation {
    type: 'pop';
}

export interface ReverseManipulation {
    type: 'reverse';
}

export type Manipulation<T> = AppendManipulation<T> | PopManipulation | ReverseManipulation;