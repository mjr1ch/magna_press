// Script parameters
    numpy_images = Channel.fromPath('./images/*.npy')
    project_dir = projectDir

process convert_images {

    echo true 
    
    input:
        file image from numpy_images

    shell:
    '''
    echo 'processing !{image}'
    python3 !{project_dir}/file_shrinker.py !{image} !{project_dir}
    rm !{project_dir}/images/!{image}
    '''
}