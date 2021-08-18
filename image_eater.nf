// Script parameters
    numpy_images = Channel.fromPath('./images/*.npy')
    project_dir = projectDir

process grab_images {

    echo true 
    
    input:
        file image from numpy_images

    shell:
    '''
    python3 --version
    echo 'processing !{image}'
    python3 !{project_dir}/k_means2.py !{image} !{project_dir}
    '''
}