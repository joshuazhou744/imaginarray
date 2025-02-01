// manipulationTypes.ts

export interface AppendManipulation<T> {
    type: 'append';
    value: T;
}

export interface PopManipulation {
    type: 'pop';
    value: null;
}

export type Manipulation<T> = AppendManipulation<T> | PopManipulation;