// manipulationTypes.ts

export interface AppendManipulation<T> {
    type: 'append';
    value: T;
}

export type Manipulation<T> = AppendManipulation<T>;