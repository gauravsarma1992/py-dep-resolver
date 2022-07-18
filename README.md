# Dependency Resolver

## Steps to resolve an Object

### Input
- Provide the file path and the object name. The object can be
of any format, i.e a class, function, variable, etc.
- Provide the folder path where the result of dependency resolver should
construct the object and its dependencies, i.e the output folder

### Processing
- Read the file to check the imports already present in the file
- Copy the object text element to the provided input folder. The path inside the
folder should be created dynamically. Ensure that the text element is added to
the existing path and not overridden
- Get the text element of the object and convert it into tokens
- Match the tokens in the imported list and the tokens of the object. If there
are cross module imports, then convert the imported object to a file path and
object combination similar to the input
- Repeat the Processing steps again
- This should ensure all the dependencies are picked up

### Output
- A similar hierarchy is created inside the output folder. For example, if we
provide `<base_folder>/models/__init__.py::<Object>` as the object, then the same path
is created inside the output folder as well
- The dependencies also follow the same structure
